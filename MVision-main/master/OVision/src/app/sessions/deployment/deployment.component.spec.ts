import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeploymentComponent } from './deployment.component';

describe('DeploymentComponent', () => {
  let component: DeploymentComponent;
  let fixture: ComponentFixture<DeploymentComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DeploymentComponent]
    });
    fixture = TestBed.createComponent(DeploymentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
