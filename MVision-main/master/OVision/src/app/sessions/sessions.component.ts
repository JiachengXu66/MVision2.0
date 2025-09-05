import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { SwitchStatusService } from './switch-status.service';
import { GetDeploymentsService } from './get-deployments.service';
import { GetMapService } from '../passive/get-maps.service';
import { Deployment } from 'src/shared/models/Entities';

@Component({
  selector: 'app-sessions',
  templateUrl: './sessions.component.html',
  styleUrls: ['./sessions.component.sass']
})
export class SessionsComponent implements OnInit {
  deploymentSessions: Deployment[] = [];
  currentPage: number = 1;
  itemsPerPage: number = 4;
  maxLength: number = 1;
  constructor(private cdr: ChangeDetectorRef,
    private getDeploymentsService: GetDeploymentsService,
    private switchStatusService: SwitchStatusService,
    private mapService: GetMapService) { }

  ngOnInit() {
    console.log("Updating pages")
    this.fetchDeploymentCount();
    this.fetchDeployments();
  } 

  onPageChange(newPage: number) {
    this.currentPage = newPage;
    console.log(this.currentPage)
    this.fetchDeployments();
  }

  switchStatusValue(session: Deployment){
    this.switchStatusService.switchStatus(session).subscribe({
      next: (response) => {
      this.fetchDeployments()
      this.cdr.detectChanges()
      console.log(response)},
      error: (error) => console.error('Error:', error),}); 
  }

  fetchDeploymentCount(){
    this.mapService.fetchCountMap().subscribe(countMaps => {
      console.log(countMaps);
      console.log(countMaps[0])
      const countMap = countMaps[0]?.get_count_map;
      if (countMap) {
        console.log(countMap);
        console.log(countMap['deployment_count']);
        this.maxLength = countMap['deployment_count'];
        console.log(this.maxLength)
        this.cdr.detectChanges();
      } else {
        console.log('Count not retrieved');
      }
    });
  }

  fetchDeployments() {
    this.getDeploymentsService.getDeployments(this.itemsPerPage, this.currentPage).subscribe({
      next: (data: any[]) => {
        this.deploymentSessions = [];
        const deployments = data.flatMap(item => item.get_latest_deployments).map(deployment => {
          return new Deployment(
            deployment.deployment_id, 
            deployment.deployment_name,
            deployment.target_id,
            deployment.status_value,
            deployment.model_id,
            new Date(deployment.creation_date), 
            new Date(deployment.start_date),
            new Date(deployment.expiry_date),
            deployment.node_id,
            deployment.device_id
          );
        });
        this.deploymentSessions = deployments;
      },
      error: (error) => console.error('Error fetching deployments:', error)
    });
  }
}
