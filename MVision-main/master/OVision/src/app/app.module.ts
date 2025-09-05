import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgxEchartsModule } from 'ngx-echarts';
import * as echarts from 'echarts';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { PaginationComponent } from './pagination/pagination.component';
import { SessionsComponent } from './sessions/sessions.component';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { ReportComponent } from './reports/report/report.component';
import { ReportsComponent } from './reports/reports.component';
import { LineGraphComponent } from './reports/graphs/line-graph/line-graph.component';
import { BarGraphComponent } from './reports/graphs/bar-graph/bar-graph.component';
import { TargetComponent } from './targets/targets.component';
import { CreateTargetComponent } from './targets/create-target/create-target.component';
import { CreateDeploymentComponent } from './sessions/create-deployment/create-deployment.component';
import { DeploymentComponent } from './sessions/deployment/deployment.component';
import { ModelsComponent } from './models/models.component';
import { CreateModelsComponent } from './models/create-models/create-models.component';
import { ModelPopupComponent } from './models/model-popup/model-popup.component';
import { NodesComponent } from './nodes/nodes.component';
import { CreateReportComponent } from './reports/create-report/create-report.component';
import { LineMultiClassComponent } from './reports/graphs/line-multi-class/line-multi-class.component';

@NgModule({
  declarations: [
    AppComponent,
    PaginationComponent,
    SessionsComponent,
    LoginComponent,
    HomeComponent,
    ReportComponent,
    ReportsComponent,
    LineGraphComponent,
    BarGraphComponent,
    TargetComponent,
    CreateTargetComponent,
    CreateDeploymentComponent,
    DeploymentComponent,
    ModelsComponent,
    CreateModelsComponent,
    ModelPopupComponent,
    NodesComponent,
    CreateReportComponent,
    LineMultiClassComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgxEchartsModule.forRoot({
      echarts,
    }), 
    FormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
